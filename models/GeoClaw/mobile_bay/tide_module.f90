module tide_module
    implicit none

    logical, save :: setup = .false.

    contains

    subroutine setup_tide(time_input, water_level, wl_size)
        integer, intent(in out) :: wl_size
        real(kind=8), dimension (:), allocatable, intent(in out) :: time_input, water_level

        integer :: iunit, i, istat
        logical :: foundFile
        character(len=255) :: wl_input
        real(kind=8), dimension (:,:), allocatable :: data_array
        real(kind=8) :: tmp

        if (.not. setup) then
            iunit = 40
            wl_input = '../tide.data'

            inquire(file=trim(adjustl(wl_input)), exist=foundFile)
            if (.not. foundFile) then
              write(*,*) 'Missing water level data file ...'
              write(*,*) 'Looking for ', trim(adjustl(wl_input)),' file'
              stop
            endif

            open(iunit, file=trim(adjustl(wl_input)), status='old', iostat=istat)

            rewind(iunit)
            wl_size = 0
            do
                read(iunit, *, iostat=istat) tmp
                if (is_iostat_end(istat)) exit
                wl_size = wl_size + 1
            end do

            allocate(data_array(wl_size, 2))
            allocate(time_input(wl_size))
            allocate(water_level(wl_size))

            rewind(iunit)
            do i= 1, wl_size
                read(iunit, *, iostat=istat) data_array(i,:)
            end do

            close(unit=iunit, iostat=istat)

            time_input(:) = data_array(:,1)
            water_level(:) = data_array(:,2)

            deallocate(data_array)

            setup = .true.
        end if

    end subroutine setup_tide

    subroutine parabola_val2(ndata, tdata, ydata, left, tval, yval)

    !*****************************************************************************80
    !
    !! PARABOLA_VAL2 evaluates a parabolic interpolant through tabular data.
    !
    !  Discussion:
    !
    !    This routine is a utility routine used by OVERHAUSER_SPLINE_VAL.
    !    It constructs the parabolic interpolant through the data in
    !    3 consecutive entries of a table and evaluates this interpolant
    !    at a given abscissa value.
    !
    !  Licensing:
    !
    !    This code is distributed under the GNU LGPL license.
    !
    !  Modified:
    !
    !    26 January 2004
    !
    !  Author:
    !
    !    John Burkardt
    !
    !  Parameters:
    !
    !    Input, integer(kind=4) :: NDATA, the number of data points.
    !    NDATA must be at least 3.
    !
    !    Input, real(kind=8) :: TDATA(NDATA), the abscissas of the data
    !    points.  The values in TDATA must be in strictly ascending order.
    !
    !    Input, real(kind=8) :: YDATA(DIM_NUM,NDATA), the data points
    !    corresponding to the abscissas.
    !
    !    Input, integer(kind=4) :: LEFT, the location of the first of the three
    !    consecutive data points through which the parabolic interpolant
    !    must pass.  1 <= LEFT <= NDATA - 2.
    !
    !    Input, real(kind=8) :: TVAL, the value of T at which the parabolic
    !    interpolant is to be evaluated.  Normally, TDATA(1) <= TVAL <= T(NDATA),
    !    and the data will be interpolated.  For TVAL outside this range,
    !    extrapolation will be used.
    !
    !    Output, real(kind=8) :: YVAL(DIM_NUM), the value of the parabolic
    !    interpolant at TVAL.
        !
        implicit none

        integer(kind=4) :: ndata

        real(kind=8) :: dif1
        real(kind=8) :: dif2
        integer(kind=4) :: left
        real(kind=8) :: t1
        real(kind=8) :: t2
        real(kind=8) :: t3
        real(kind=8) :: tval
        real(kind=8) :: tdata(ndata)
        real(kind=8) :: ydata(ndata)
        real(kind=8) :: y1
        real(kind=8) :: y2
        real(kind=8) :: y3
        real(kind=8) :: yval
        !
        !  Check.
        !
        if (left < 1) then
        write (*, '(a)') ' '
        write (*, '(a)') 'PARABOLA_VAL2 - Fatal error!'
        write (*, '(a)') '  LEFT < 1.'
        write (*, '(a,i8)') '  LEFT = ', left
        stop 1
        end if

        if (ndata-2 < left) then
        write (*, '(a)') ' '
        write (*, '(a)') 'PARABOLA_VAL2 - Fatal error!'
        write (*, '(a)') '  NDATA-2 < LEFT.'
        write (*, '(a,i8)') '  NDATA = ', ndata
        write (*, '(a,i8)') '  LEFT =  ', left
        stop 1
        end if
        !
        !  Copy out the three abscissas.
        !
        t1 = tdata(left)
        t2 = tdata(left+1)
        t3 = tdata(left+2)

        if (t2 <= t1 .or. t3 <= t2) then
        write(*, '(a)') ' '
        write(*, '(a)') 'PARABOLA_VAL2 - Fatal error!'
        write(*, '(a)') '  T2 <= T1 or T3 <= T2.'
        stop 1
        end if
        !
        !  Construct and evaluate a parabolic interpolant for the data
        !  in each dimension.
        !

        y1 = ydata(left)
        y2 = ydata(left+1)
        y3 = ydata(left+2)

        dif1 = (y2 - y1) / (t2 - t1)
        dif2 = ((y3 - y1) / (t3 - t1) &
            - (y2 - y1) / (t2 - t1)) / (t3 - t2)
        yval = y1 + (tval - t1) * (dif1 + (tval - t2) * dif2)

        return
    end subroutine parabola_val2

    subroutine linear_val2(y, t, y1, y2, t1, t2)

        implicit none
        real(kind=8), intent(in) :: t, y1, y2, t1, t2
        real(kind=8), intent(out) :: y

        if (t1 > t2) then
            print *, 'Fatal error, t1 > t2'
            stop
        end if

        y = y1 + (y2 - y1) / (t2 - t1) * (t - t1)

      return
    end subroutine linear_val2

end module tide_module
